import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY", "1611882205be3979e2cc2c83a5265c1882838dd59ce222f77b3cd4cfc2ac6dea")
    FAL_API_KEY = os.getenv("FAL_API_KEY", "b6aa8a34-dc84-4bd5-9b7e-c4b46ad4b31c:b8b67a1d8a8e7d10d92df97b5c9c0c6e")
    
    # API Endpoints
    WAVESPEED_BASE_URL = os.getenv("WAVESPEED_BASE_URL", "https://api.wavespeed.ai/api/v3")
    WAVESPEED_MODEL = os.getenv("WAVESPEED_MODEL", "bytedance/seedance-v1-pro-t2v-480p")
    
    # FAL AI Models
    FAL_AUDIO_MODEL = os.getenv("FAL_AUDIO_MODEL", "fal-ai/mmaudio-v2")
    FAL_FFMPEG_MODEL = os.getenv("FAL_FFMPEG_MODEL", "fal-ai/ffmpeg-api/compose")
    
    # Generation Settings
    TEXT_MODEL = os.getenv("TEXT_MODEL", "gpt-4o-mini")
    CARTOON_STYLE = os.getenv("CARTOON_STYLE", "2D cartoon animation, Disney style, vibrant colors, smooth animation")
    DEFAULT_DURATION = int(os.getenv("DEFAULT_DURATION", "30"))
    VIDEO_ASPECT_RATIO = os.getenv("VIDEO_ASPECT_RATIO", "9:16")
    VIDEO_RESOLUTION = os.getenv("VIDEO_RESOLUTION", "480p")
    
    # Server Settings
    HOST = os.getenv("HOST", "localhost")
    PORT = int(os.getenv("PORT", "8007"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    
    # JWT Authentication
    JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
    
    # Cache Settings
    CACHE_DIR = Path(os.getenv("CACHE_DIR", "../cache"))
    MAX_CACHE_SIZE_GB = int(os.getenv("MAX_CACHE_SIZE_GB", "10"))
    CACHE_CLEANUP_HOURS = int(os.getenv("CACHE_CLEANUP_HOURS", "24"))
    
    @classmethod
    def validate_api_keys(cls):
        """Valide que les clés API essentielles sont configurées"""
        missing_keys = []
        
        if not cls.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if not cls.WAVESPEED_API_KEY:
            missing_keys.append("WAVESPEED_API_KEY")
        if not cls.FAL_API_KEY:
            missing_keys.append("FAL_API_KEY")
            
        if missing_keys:
            raise ValueError(f"Clés API manquantes: {', '.join(missing_keys)}")
        
        return True

# Instance globale de configuration
config = Config() 