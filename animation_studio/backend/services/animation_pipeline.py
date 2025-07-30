import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from config import config
from models.schemas import (
    AnimationRequest, AnimationResult, AnimationProgress, AnimationStatus,
    StoryIdea, Scene, VideoClip, AudioTrack, AnimationTheme
)
from .idea_generator import IdeaGenerator
from .scene_creator import SceneCreator
from .video_generator import VideoGenerator
from .audio_generator import AudioGenerator
from .video_assembler import VideoAssembler

class AnimationPipeline:
    """Pipeline principal de génération de dessins animés (inspiré de zseedance.json)"""
    
    def __init__(self):
        self.idea_generator = IdeaGenerator()
        self.scene_creator = SceneCreator()
        self.video_generator = VideoGenerator()
        self.audio_generator = AudioGenerator()
        self.video_assembler = VideoAssembler()
        
        # Cache pour suivre les animations en cours
        self.active_animations: Dict[str, AnimationResult] = {}
    
    async def generate_animation(
        self, 
        request: AnimationRequest, 
        progress_callback: Optional[Callable[[AnimationProgress], None]] = None
    ) -> AnimationResult:
        """Génère un dessin animé complet selon le workflow zseedance.json"""
        
        # Initialiser le résultat
        animation_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = AnimationResult(
            animation_id=animation_id,
            status=AnimationStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        self.active_animations[animation_id] = result
        
        try:
            # Étape 1: Génération d'idée (équivalent "Ideas AI Agent" dans n8n)
            await self._update_progress(animation_id, AnimationStatus.GENERATING_IDEA, 10, 
                                      "Génération de l'idée d'histoire...", progress_callback)
            
            story_idea = await self.idea_generator.generate_story_idea(request.theme, request.duration)
            
            # Valider l'idée pour les enfants
            if not await self.idea_generator.validate_idea(story_idea):
                raise Exception("L'idée générée n'est pas appropriée pour les enfants")
            
            result.story_idea = story_idea
            
            # Étape 2: Création des scènes (équivalent "Prompts AI Agent" dans n8n)
            await self._update_progress(animation_id, AnimationStatus.CREATING_SCENES, 25,
                                      "Création des scènes détaillées...", progress_callback)
            
            scenes = await self.scene_creator.create_scenes_from_idea(story_idea, request.duration)
            result.scenes = scenes
            
            # Étape 3: Génération des clips vidéo (équivalent "Create Clips" -> "Get Clips" dans n8n)
            await self._update_progress(animation_id, AnimationStatus.GENERATING_CLIPS, 40,
                                      "Génération des clips vidéo...", progress_callback)
            
            video_clips = await self.video_generator.generate_all_clips(scenes)
            result.video_clips = video_clips
            
            # Vérifier qu'au moins un clip a été généré avec succès
            valid_clips = [clip for clip in video_clips if clip.status == "completed"]
            if not valid_clips:
                raise Exception("Aucun clip vidéo n'a pu être généré")
            
            # Étape 4: Génération audio (équivalent "Create Sounds" -> "Get Sounds" dans n8n)
            await self._update_progress(animation_id, AnimationStatus.GENERATING_AUDIO, 70,
                                      "Génération des effets sonores...", progress_callback)
            
            try:
                audio_track = await self.audio_generator.generate_audio_for_video(
                    story_idea, video_clips, request.duration
                )
                result.audio_track = audio_track
            except Exception as e:
                # Audio optionnel - continuer sans audio en cas d'échec
                print(f"Avertissement: Échec génération audio: {e}")
                result.audio_track = None
            
            # Étape 5: Assemblage final (équivalent "Sequence Video" -> "Get Final Video" dans n8n)
            await self._update_progress(animation_id, AnimationStatus.ASSEMBLING_VIDEO, 85,
                                      "Assemblage de la vidéo finale...", progress_callback)
            
            try:
                final_video_url = await self.video_assembler.assemble_final_video(
                    video_clips, result.audio_track
                )
            except Exception as e:
                # Fallback: créer une séquence simple sans audio
                print(f"Échec assemblage complet, essai séquence simple: {e}")
                final_video_url = await self.video_assembler.create_simple_sequence(video_clips)
            
            if not final_video_url:
                # Dernière solution: retourner le premier clip valide
                final_video_url = next((clip.video_url for clip in valid_clips), "")
            
            result.final_video_url = final_video_url
            
            # Finalisation
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.status = AnimationStatus.COMPLETED
            
            await self._update_progress(animation_id, AnimationStatus.COMPLETED, 100,
                                      "Animation terminée!", progress_callback)
            
            return result
            
        except Exception as e:
            # Gestion d'erreur
            result.status = AnimationStatus.FAILED
            result.error_message = str(e)
            
            await self._update_progress(animation_id, AnimationStatus.FAILED, 0,
                                      f"Erreur: {str(e)}", progress_callback)
            
            return result
        
        finally:
            # Nettoyer le cache
            if animation_id in self.active_animations:
                self.active_animations[animation_id] = result

    async def _update_progress(
        self, 
        animation_id: str, 
        status: AnimationStatus, 
        percentage: int,
        current_step: str,
        callback: Optional[Callable[[AnimationProgress], None]] = None
    ):
        """Met à jour la progression et appelle le callback si fourni"""
        
        progress = AnimationProgress(
            animation_id=animation_id,
            status=status,
            progress_percentage=percentage,
            current_step=current_step
        )
        
        # Estimer le temps restant
        if status != AnimationStatus.COMPLETED and status != AnimationStatus.FAILED:
            estimated_total_time = self.estimate_total_generation_time()
            remaining_time = int(estimated_total_time * (100 - percentage) / 100)
            progress.estimated_remaining_time = remaining_time
        
        if callback:
            callback(progress)

    def get_animation_status(self, animation_id: str) -> Optional[AnimationResult]:
        """Récupère le statut d'une animation en cours"""
        return self.active_animations.get(animation_id)

    def estimate_total_generation_time(self) -> int:
        """Estime le temps total de génération en secondes"""
        
        # Basé sur l'expérience du workflow zseedance.json
        idea_time = 30          # Génération d'idée: 30s
        scenes_time = 45        # Création scènes: 45s
        video_time = 300        # Génération vidéo: 5 minutes (le plus long)
        audio_time = 90         # Génération audio: 1.5 minutes
        assembly_time = 120     # Assemblage: 2 minutes
        
        return idea_time + scenes_time + video_time + audio_time + assembly_time

    async def validate_pipeline_health(self) -> Dict[str, Any]:
        """Valide que tous les services du pipeline sont opérationnels"""
        
        health_check = {
            "pipeline_operational": True,
            "services": {},
            "estimated_generation_time": self.estimate_total_generation_time()
        }
        
        # Tester OpenAI (vérification de clé seulement, pas d'appel API)
        try:
            # Vérification rapide des clés sans appel API
            if config.OPENAI_API_KEY and config.OPENAI_API_KEY.startswith("sk-"):
                health_check["services"]["idea_generator"] = {"status": "configured", "test": "key_valid"}
            else:
                raise ValueError("Clé OpenAI invalide ou manquante")
        except Exception as e:
            health_check["services"]["idea_generator"] = {"status": "failed", "error": str(e)}
            health_check["pipeline_operational"] = False
        
        # Tester Wavespeed (génération vidéo)
        health_check["services"]["video_generator"] = {
            "status": "configured" if config.WAVESPEED_API_KEY else "missing_api_key",
            "model": config.WAVESPEED_MODEL
        }
        
        # Tester FAL AI (audio et assemblage)
        health_check["services"]["audio_generator"] = {
            "status": "configured" if config.FAL_API_KEY else "missing_api_key",
            "model": config.FAL_AUDIO_MODEL
        }
        
        health_check["services"]["video_assembler"] = {
            "status": "configured" if config.FAL_API_KEY else "missing_api_key",
            "model": config.FAL_FFMPEG_MODEL
        }
        
        return health_check

    def get_supported_themes(self) -> Dict[str, Dict[str, str]]:
        """Retourne les thèmes supportés avec leurs descriptions"""
        return self.idea_generator.get_theme_prompts()

    def cleanup_old_animations(self, max_age_hours: int = 24):
        """Nettoie les anciennes animations du cache"""
        current_time = time.time()
        
        to_remove = []
        for animation_id, result in self.active_animations.items():
            creation_time = datetime.fromisoformat(result.created_at).timestamp()
            if current_time - creation_time > (max_age_hours * 3600):
                to_remove.append(animation_id)
        
        for animation_id in to_remove:
            del self.active_animations[animation_id] 