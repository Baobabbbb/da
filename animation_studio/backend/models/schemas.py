from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class AnimationTheme(str, Enum):
    """Thèmes prédéfinis pour les dessins animés"""
    SPACE = "space"
    NATURE = "nature"
    ADVENTURE = "adventure"
    ANIMALS = "animals"
    MAGIC = "magic"
    FRIENDSHIP = "friendship"

class AnimationDuration(int, Enum):
    """Durées disponibles en secondes"""
    THIRTY_SEC = 30
    ONE_MIN = 60
    TWO_MIN = 120
    THREE_MIN = 180
    FOUR_MIN = 240
    FIVE_MIN = 300

class AnimationStatus(str, Enum):
    """États de traitement de l'animation"""
    PENDING = "pending"
    GENERATING_IDEA = "generating_idea"
    CREATING_SCENES = "creating_scenes"
    GENERATING_CLIPS = "generating_clips"
    GENERATING_AUDIO = "generating_audio"
    ASSEMBLING_VIDEO = "assembling_video"
    COMPLETED = "completed"
    FAILED = "failed"

class AnimationRequest(BaseModel):
    """Requête de génération d'animation"""
    theme: AnimationTheme
    duration: AnimationDuration
    user_id: Optional[str] = None
    custom_prompt: Optional[str] = None

class StoryIdea(BaseModel):
    """Idée d'histoire générée"""
    caption: str
    idea: str
    environment: str
    sound: str
    status: str = "for production"

class Scene(BaseModel):
    """Scène individuelle de l'animation"""
    scene_number: int
    description: str
    duration: int
    prompt: str

class VideoClip(BaseModel):
    """Clip vidéo généré"""
    scene_number: int
    video_url: str
    duration: int
    status: str

class AudioTrack(BaseModel):
    """Piste audio générée"""
    audio_url: str
    duration: int
    description: str

class AnimationResult(BaseModel):
    """Résultat final de l'animation"""
    animation_id: str
    status: AnimationStatus
    story_idea: Optional[StoryIdea] = None
    scenes: Optional[List[Scene]] = None
    video_clips: Optional[List[VideoClip]] = None
    audio_track: Optional[AudioTrack] = None
    final_video_url: Optional[str] = None
    created_at: str
    processing_time: Optional[float] = None
    error_message: Optional[str] = None

class AnimationProgress(BaseModel):
    """Progression du traitement"""
    animation_id: str
    status: AnimationStatus
    progress_percentage: int = Field(ge=0, le=100)
    current_step: str
    estimated_remaining_time: Optional[int] = None  # en secondes
    details: Optional[Dict[str, Any]] = None

class DiagnosticResponse(BaseModel):
    """Réponse de diagnostic des APIs"""
    openai_configured: bool
    wavespeed_configured: bool
    fal_configured: bool
    all_systems_operational: bool
    details: Dict[str, Any] 