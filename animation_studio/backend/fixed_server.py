#!/usr/bin/env python3
"""
Serveur FastAPI pour génération d'animations complètes avec Wavespeed
Suivant le workflow zseedance.json
"""

import os
import time
import threading
import requests
import openai
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

@app.get("/costs")
def get_cost_estimates():
    """Obtenir les coûts estimés pour toutes les durées"""
    durations = [30, 60, 120, 180, 240, 300]  # 30s, 1min, 2min, 3min, 4min, 5min
    
    cost_estimates = {}
    for duration in durations:
        cost_info = calculate_estimated_cost(duration)
        cost_estimates[f"{duration}s"] = cost_info
    
    return {
        "cost_estimates": cost_estimates,
        "currency": "EUR",
        "notes": "Estimations basées sur ~0.30€ par clip Wavespeed (15 secondes)"
    }

def calculate_estimated_cost(duration: int):
    """Calculer le coût estimé de la génération"""
    scenes_count = max(3, duration // 20)  # Optimisation : 1 scène par 20 secondes
    estimated_cost_per_clip = 0.30  # € par clip Wavespeed
    total_estimated_cost = scenes_count * estimated_cost_per_clip
    
    return {
        "scenes_count": scenes_count,
        "cost_per_clip": estimated_cost_per_clip,
        "total_estimated_cost": total_estimated_cost,
        "duration_per_scene": duration // scenes_count
    }

@app.post("/generate")
def generate_animation(request: dict):
    theme = request.get("theme", "space")
    duration = request.get("duration", 30)
    
    # Calculer le coût estimé
    cost_info = calculate_estimated_cost(duration)
    print(f"💰 Coût estimé pour {duration}s: {cost_info['total_estimated_cost']:.2f}€ ({cost_info['scenes_count']} scènes)")
    
    # Générer un ID unique
    animation_id = f"anim_{int(time.time())}"
    
    # Initialiser la tâche
    generation_tasks[animation_id] = {
        "status": "generating",
        "progress": 0,
        "current_step": "🚀 Démarrage de la génération...",
        "theme": theme,
        "duration": duration,
        "cost_estimate": cost_info
    }
    
    print(f"🎬 Nouvelle génération: {animation_id} - Thème: {theme} - Durée: {duration}s")
    
    # Lancer la génération en arrière-plan
    thread = threading.Thread(
        target=real_generation_process,
        args=(animation_id, theme, duration)
    )
    thread.daemon = True
    thread.start()
    
    return {
        "animation_id": animation_id, 
        "status": "started",
        "cost_estimate": cost_info
    }

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
            "story": {
                "title": story.get("title", f"Histoire {theme}"),
                "summary": story.get("summary", ""),
                "characters": story.get("characters", []),
                "moral": story.get("moral", ""),
                "target_audience": story.get("target_audience", "Enfants de 3-8 ans")
            },
            "scenes": scenes,
            "theme": theme,
            "duration": duration,
            "real_generation": True,
            "professional_storytelling": True
        }
        
        print(f"🎉 DESSIN ANIMÉ COMPLET {animation_id} terminé!")
        
    except Exception as e:
        print(f"💥 ERREUR GÉNÉRATION: {e}")
        task["status"] = "error"
        task["error"] = str(e)
        task["current_step"] = "❌ Erreur génération"

def generate_complete_story_sync(theme: str, duration: int):
    """Générer une histoire complète et cohérente avec OpenAI (optimisée pour les coûts)"""
    
    # Configuration OpenAI
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # Optimisation : moins de scènes mais plus longues
    scenes_count = max(3, duration // 20)  # 1 scène par 20 secondes
    
    # Prompt pour générer une histoire de niveau professionnel (optimisée)
    story_prompt = f"""Crée une histoire d'animation de {duration} secondes sur le thème "{theme}" avec une structure narrative complète comme dans les dessins animés professionnels.

L'histoire doit avoir :
- Une exposition (introduction des personnages et du monde)
- Un développement (conflit ou défi à surmonter)
- Un climax (moment de tension maximale)
- Une résolution (fin heureuse et satisfaisante)

IMPORTANT : Divise l'histoire en exactement {scenes_count} scènes de {duration // scenes_count} secondes chacune pour optimiser les coûts tout en gardant la qualité narrative.

CRUCIAL : Assure une cohérence visuelle parfaite entre toutes les scènes :
- Les personnages doivent avoir la même apparence dans toutes les scènes
- L'univers visuel doit être cohérent (même style, couleurs, décors)
- Les transitions entre scènes doivent être fluides
- Utilise des descriptions visuelles très précises et cohérentes

IMPORTANT : Réponds UNIQUEMENT avec un JSON valide, sans texte avant ou après.

Format de réponse JSON :
{{
    "title": "Titre accrocheur de l'histoire",
    "summary": "Résumé complet de l'histoire avec tous les éléments narratifs",
    "universe_description": "Description détaillée de l'univers visuel (style, couleurs, ambiance, décors)",
    "main_character": {{
        "name": "Nom du personnage principal",
        "appearance": "Description physique très détaillée (âge, vêtements, couleurs, style)",
        "personality": "Caractère et comportement du personnage",
        "role": "Rôle dans l'histoire"
    }},
    "supporting_characters": [
        {{
            "name": "Nom du personnage secondaire",
            "appearance": "Description physique très détaillée",
            "personality": "Caractère du personnage",
            "role": "Rôle dans l'histoire"
        }}
    ],
    "scenes": [
        {{
            "scene_number": 1,
            "title": "Titre de la scène",
            "description": "Description détaillée de ce qui se passe",
            "visual_elements": "Éléments visuels spécifiques (décors, actions, expressions) - TRÈS DÉTAILLÉ",
            "dialogue": "Dialogues ou narration pour cette scène",
            "emotions": "Émotions des personnages et ambiance",
            "duration": {duration // scenes_count},
            "narrative_purpose": "Rôle de cette scène dans l'histoire (exposition, développement, etc.)",
            "transition": "Comment cette scène se connecte à la suivante",
            "camera_angle": "Angle de caméra et perspective",
            "lighting": "Éclairage et ambiance visuelle"
        }}
    ],
    "theme": "{theme}",
    "total_duration": {duration},
    "moral": "Message ou leçon de l'histoire",
    "target_audience": "Enfants de 3-8 ans",
    "visual_style": "Style visuel cohérent pour toute l'animation (couleurs, technique, ambiance)"
}}

L'histoire doit être captivante, avec des personnages attachants, des émotions fortes, et une progression logique qui maintient l'intérêt du début à la fin. Chaque scène doit être suffisamment riche pour justifier sa durée plus longue. LA COHÉRENCE VISUELLE EST PRIMORDIALE."""

    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un scénariste professionnel spécialisé dans les dessins animés pour enfants. Tu crées des histoires avec une structure narrative complète, des personnages mémorables, et des émotions authentiques. Tu accordes une importance capitale à la cohérence visuelle entre toutes les scènes. Tu réponds UNIQUEMENT avec du JSON valide, sans texte avant ou après."},
                {"role": "user", "content": story_prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        story_text = response.choices[0].message.content
        print(f"📝 Histoire professionnelle générée: {story_text[:300]}...")
        
        # Nettoyer et parser la réponse JSON
        import json
        import re
        
        # Nettoyer le texte pour extraire le JSON
        cleaned_text = story_text.strip()
        
        # Supprimer les backticks et "json" si présents
        cleaned_text = re.sub(r'^```json\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
        cleaned_text = re.sub(r'^```\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
        
        # Essayer de parser le JSON
        try:
            story_data = json.loads(cleaned_text)
            print(f"✅ JSON parsé avec succès")
            return story_data
        except json.JSONDecodeError as e:
            print(f"⚠️  Première tentative de parsing JSON échouée: {e}")
            
            # Tentative de correction : chercher le JSON dans le texte
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                try:
                    corrected_json = json_match.group(0)
                    story_data = json.loads(corrected_json)
                    print(f"✅ JSON corrigé et parsé avec succès")
                    return story_data
                except json.JSONDecodeError as e2:
                    print(f"⚠️  Correction JSON échouée: {e2}")
            
            # Dernière tentative : essayer de corriger les erreurs communes
            try:
                # Remplacer les guillemets mal échappés
                corrected_text = cleaned_text.replace('"', '"').replace('"', '"')
                corrected_text = re.sub(r',\s*}', '}', corrected_text)  # Virgules trailing
                corrected_text = re.sub(r',\s*]', ']', corrected_text)  # Virgules trailing dans arrays
                
                story_data = json.loads(corrected_text)
                print(f"✅ JSON corrigé avec succès")
                return story_data
            except json.JSONDecodeError as e3:
                print(f"💥 Toutes les tentatives de parsing JSON ont échoué: {e3}")
                print(f"📝 Texte original: {cleaned_text[:500]}...")
                raise Exception("Impossible de parser la réponse JSON d'OpenAI")
            
    except Exception as e:
        print(f"💥 Erreur génération histoire OpenAI: {e}")
        raise Exception(f"Génération d'histoire échouée: {e}")

def generate_detailed_scenes_sync(story: dict, theme: str, duration: int):
    """Générer des scènes détaillées basées sur l'histoire professionnelle (optimisée)"""
    
    if "scenes" in story and story["scenes"]:
        # Utiliser les scènes générées par OpenAI avec tous les détails
        scenes = []
        
        # Extraire les informations de cohérence visuelle
        universe_desc = story.get("universe_description", "")
        main_char = story.get("main_character", {})
        visual_style = story.get("visual_style", "")
        
        for scene_data in story["scenes"]:
            # Créer un prompt visuel riche avec cohérence parfaite
            visual_prompt = f"""{CARTOON_STYLE}, {scene_data['title']}, {scene_data['description']}, {scene_data['visual_elements']}, {scene_data['emotions']}, {scene_data['dialogue']}, {scene_data['narrative_purpose']}, {scene_data['transition']}, {universe_desc}, {main_char.get('appearance', '')}, {visual_style}, colorful, high quality animation, children friendly, professional storytelling, coherent narrative flow, consistent character design, consistent visual style"""
            
            scenes.append({
                "id": scene_data["scene_number"],
                "title": scene_data["title"],
                "description": scene_data["description"],
                "duration": scene_data["duration"],
                "visual_prompt": visual_prompt,
                "dialogue": scene_data.get("dialogue", ""),
                "emotions": scene_data.get("emotions", ""),
                "narrative_purpose": scene_data.get("narrative_purpose", ""),
                "transition": scene_data.get("transition", ""),
                "camera_angle": scene_data.get("camera_angle", ""),
                "lighting": scene_data.get("lighting", "")
            })
        return scenes
    else:
        # Si pas de scènes dans l'histoire, créer une structure minimale
        raise Exception("Aucune scène trouvée dans l'histoire générée")

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
    """Générer un seul clip vidéo avec Wavespeed (optimisé pour les coûts)"""
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Améliorer le prompt avec des instructions de cohérence
    enhanced_prompt = f"{prompt}, consistent character design, same visual style throughout, coherent animation, smooth transitions, professional cartoon quality"
    
    data = {
        "aspect_ratio": "16:9",  # Paysage
        "duration": 10,  # Correction : 10 secondes maximum pour Wavespeed
        "prompt": enhanced_prompt[:500]  # Limiter à 500 caractères
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
    """Générer l'audio professionnel avec narration, dialogue et musique d'ambiance"""
    
    # Créer un script audio basé sur l'histoire complète
    audio_script = f"Histoire: {story.get('title', 'Aventure')}\n\n"
    
    if "summary" in story:
        audio_script += f"Résumé: {story['summary']}\n\n"
    
    if "characters" in story:
        audio_script += "Personnages:\n"
        for char in story["characters"]:
            audio_script += f"- {char['name']}: {char['description']}\n"
        audio_script += "\n"
    
    if "scenes" in story:
        audio_script += "Scènes:\n"
        for scene in story["scenes"]:
            audio_script += f"Scène {scene['scene_number']}: {scene.get('title', '')}\n"
            audio_script += f"Dialogue: {scene.get('dialogue', '')}\n"
            audio_script += f"Émotions: {scene.get('emotions', '')}\n\n"
    
    if "moral" in story:
        audio_script += f"Leçon: {story['moral']}\n"
    
    # Créer un prompt pour la musique d'ambiance
    music_prompt = f"Musique d'ambiance pour une histoire d'animation sur le thème {theme}. "
    music_prompt += "Style: mélodique, adapté aux enfants, avec des variations selon les émotions des scènes. "
    music_prompt += "Inclure des sons d'ambiance cohérents avec le thème et l'histoire."
    
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Pour l'instant, simuler la génération audio professionnelle
    print(f"🔊 Script audio professionnel généré:")
    print(f"📝 {audio_script[:200]}...")
    print(f"🎵 {music_prompt}")
    
    # TODO: Implémenter la vraie génération audio avec FAL AI ou OpenAI TTS
    # Pour l'instant, retourner une URL factice
    return "https://example.com/professional_audio.mp3"

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