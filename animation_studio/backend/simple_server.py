from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Animation Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Animation Studio API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

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

@app.post("/generate-quick")
async def generate_quick(theme: str, duration: int):
    return {
        "animation_id": "demo-123",
        "status": "completed",
        "final_video_url": "https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_5mb.mp4",
        "processing_time": 60,
        "story_idea": {
            "idea": f"Une belle histoire de {theme} durant {duration} secondes",
            "caption": f"Animation {theme} creee! #animation #{theme}",
            "environment": f"Univers colore de {theme}",
            "sound": "Musique douce et effets sonores melodieux"
        }
    }

if __name__ == "__main__":
    print("Backend Test - Port 8007")
    uvicorn.run(app, host="0.0.0.0", port=8007)
