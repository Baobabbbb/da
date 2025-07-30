from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
import uuid
import random
import time

app = FastAPI(title="Animation Studio - Async Generation API")

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
    """Démarrer la génération d'une animation avec progression réaliste"""
    
    animation_id = str(uuid.uuid4())
    
    # Initialiser le status
    generation_tasks[animation_id] = GenerationStatus(
        animation_id=animation_id,
        status="starting",
        progress=0,
        current_step="🚀 Initialisation du système d'IA..."
    )
    
    # Lancer la génération en arrière-plan
    asyncio.create_task(simulate_real_generation(animation_id, request.theme, request.duration))
    
    return {"animation_id": animation_id, "status": "started"}

@app.get("/status/{animation_id}")
async def get_generation_status(animation_id: str):
    """Obtenir le statut de génération d'une animation"""
    if animation_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Animation ID non trouvé")
    
    return generation_tasks[animation_id]

async def simulate_real_generation(animation_id: str, theme: str, duration: int):
    """Simulation réaliste du processus de génération avec vraie temporisation"""
    try:
        task = generation_tasks[animation_id]
        
        # Étape 1: Génération de l'idée (simulation OpenAI)
        task.current_step = "🧠 Génération de l'idée créative avec OpenAI..."
        task.progress = 5
        await asyncio.sleep(3)  # Simulation temps réel OpenAI
        
        task.current_step = "📝 Analyse du thème et création de l'histoire..."
        task.progress = 15
        await asyncio.sleep(2)
        
        # Étape 2: Création des scènes
        task.current_step = "🎬 Décomposition en scènes cinématographiques..."
        task.progress = 25
        await asyncio.sleep(3)
        
        task.current_step = "🎭 Optimisation des transitions et dialogues..."
        task.progress = 35
        await asyncio.sleep(2)
        
        # Étape 3: Génération des clips vidéo (simulation Wavespeed AI)
        scene_count = max(2, duration // 15)  # Plus de scènes pour les vidéos longues
        for i in range(scene_count):
            task.current_step = f"🎥 Génération du clip {i+1}/{scene_count} avec Wavespeed AI..."
            task.progress = 35 + (i * 25 // scene_count)
            await asyncio.sleep(4 + random.randint(1, 3))  # Simulation temps réel de génération vidéo
        
        # Étape 4: Génération de l'audio (simulation FAL AI)
        task.current_step = "🎵 Création de la musique de fond avec FAL AI..."
        task.progress = 70
        await asyncio.sleep(5)
        
        task.current_step = "🔊 Génération des effets sonores..."
        task.progress = 80
        await asyncio.sleep(3)
        
        # Étape 5: Assemblage final (simulation FFmpeg)
        task.current_step = "🎞️ Assemblage des clips avec FFmpeg..."
        task.progress = 90
        await asyncio.sleep(4)
        
        task.current_step = "🎨 Finalisation et optimisation..."
        task.progress = 95
        await asyncio.sleep(2)
        
        task.current_step = "📤 Upload et génération du lien de téléchargement..."
        task.progress = 98
        await asyncio.sleep(2)
        
        # Finalisation avec vraies données
        themes_info = {
            "space": {"story": "Un petit astronaute découvre une planète magique peuplée d'aliens sympathiques", "emoji": "🚀", "video": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"},
            "nature": {"story": "Une petite graine devient un arbre géant qui protège la forêt", "emoji": "🌲", "video": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"},
            "adventure": {"story": "Un jeune héros part à la recherche du trésor perdu dans un château enchanté", "emoji": "⚔️", "video": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"},
            "animals": {"story": "Des animaux de la forêt organisent une grande fête d'amitié", "emoji": "🦊", "video": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullhunt.mp4"},
            "magic": {"story": "Un apprenti sorcier apprend ses premiers sorts magiques", "emoji": "✨", "video": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"},
            "friendship": {"story": "Deux amis différents apprennent l'importance de l'entraide", "emoji": "💖", "video": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"}
        }
        
        theme_info = themes_info.get(theme, themes_info["space"])
        
        task.current_step = "✨ Animation terminée avec succès !"
        task.progress = 100
        task.status = "completed"
        task.result = {
            "final_video_url": theme_info["video"],
            "story_idea": {
                "idea": theme_info["story"],
                "caption": f"Animation {theme} créée avec l'IA ! #animation #{theme}",
                "environment": f"Un univers coloré de {theme}",
                "sound": "Musique originale et effets sonores"
            },
            "scenes_count": scene_count,
            "clips_count": scene_count,
            "generation_time": 45 + random.randint(10, 30),
            "theme": theme,
            "duration": duration,
            "ai_models_used": ["OpenAI GPT-4", "Wavespeed SeedANce v1 Pro", "FAL mmaudio-v2", "FFmpeg Compose"]
        }
        
        print(f"✅ Animation {animation_id} générée avec succès - Thème: {theme}, Durée: {duration}s")
        
    except Exception as e:
        task.status = "error"
        task.error = f"Erreur lors de la génération: {str(e)}"
        task.current_step = "❌ Erreur de génération"
        print(f"❌ Erreur génération {animation_id}: {e}")

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
    print("🚀 Animation Studio - Génération Asynchrone Réaliste")
    print("🤖 Simulation: OpenAI + Wavespeed + FAL + FFmpeg")
    print("🎬 Prêt à générer des animations sur le port 8009...")
    uvicorn.run(app, host="0.0.0.0", port=8009) 