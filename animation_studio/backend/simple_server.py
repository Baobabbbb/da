from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Animation Studio API")

# Configuration CORS simple
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Animation Studio API - Serveur de test"}

@app.get("/diagnostic")
async def diagnostic():
    return {
        "openai_configured": True,
        "wavespeed_configured": True,
        "fal_configured": True,
        "all_systems_operational": True,
        "details": {"test": "Server is running"}
    }

@app.get("/themes")
async def get_themes():
    return {
        "themes": {
            "space": {"name": "Space", "description": "Aventure spatiale", "icon": "🚀"},
            "nature": {"name": "Nature", "description": "Aventure nature", "icon": "🌳"},
            "adventure": {"name": "Adventure", "description": "Aventure héroïque", "icon": "🏰"}
        },
        "durations": [30, 60, 120],
        "default_duration": 30
    }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8008, log_level="info")
