import asyncio
import aiohttp
from typing import List, Dict, Any
from config import config
from models.schemas import StoryIdea, VideoClip, AudioTrack

class AudioGenerator:
    """Service de génération audio via FAL AI (basé sur mmaudio-v2 du workflow zseedance.json)"""
    
    def __init__(self):
        self.fal_api_key = config.FAL_API_KEY
        self.audio_model = config.FAL_AUDIO_MODEL
        self.base_url = "https://queue.fal.run"
    
    async def generate_audio_for_video(self, story_idea: StoryIdea, video_clips: List[VideoClip], total_duration: int) -> AudioTrack:
        """Génère une piste audio complète pour la vidéo"""
        
        # Adapter le prompt audio pour les enfants (basé sur zseedance.json mais modifié)
        audio_prompt = self.create_child_friendly_audio_prompt(story_idea)
        
        try:
            # 1. Soumettre la requête de génération audio
            audio_data = await self._submit_audio_generation(audio_prompt, total_duration, video_clips)
            
            if not audio_data or "request_id" not in audio_data:
                raise Exception("Réponse invalide de l'API FAL AI")
            
            request_id = audio_data["request_id"]
            
            # 2. Attendre le traitement (équivalent du "Wait for Sounds" dans n8n)
            await asyncio.sleep(min(total_duration * 3, 60))  # Attente adaptative
            
            # 3. Récupérer le résultat
            result = await self._get_audio_result(request_id)
            
            if not result or "audio_url" not in result:
                raise Exception("Erreur lors de la récupération de l'audio")
            
            return AudioTrack(
                audio_url=result["audio_url"],
                duration=total_duration,
                description=audio_prompt
            )
            
        except Exception as e:
            # Retourner une piste audio silencieuse en cas d'erreur
            return AudioTrack(
                audio_url="",
                duration=total_duration,
                description=f"Audio generation failed: {str(e)}"
            )

    def create_child_friendly_audio_prompt(self, story_idea: StoryIdea) -> str:
        """Crée un prompt audio adapté aux enfants (inspiré mais modifié depuis zseedance.json)"""
        
        # Remplacer les éléments "aliens" du workflow original par des éléments enfantins
        base_sound = story_idea.sound
        
        # Mots-clés enfants pour remplacer les termes "dramatiques" du workflow original
        child_friendly_terms = {
            "dramatic": "gentle and playful",
            "cinematic": "magical and wonder-filled", 
            "strange": "curious and interesting",
            "alien": "magical creature",
            "mysterious": "enchanting",
            "intense": "exciting",
            "powerful": "joyful"
        }
        
        # Nettoyer et adapter le prompt
        adapted_sound = base_sound.lower()
        for old_term, new_term in child_friendly_terms.items():
            adapted_sound = adapted_sound.replace(old_term, new_term)
        
        # Structure finale inspirée du workflow zseedance.json mais adaptée
        final_prompt = f"sound effects: {adapted_sound}. Gentle, magical, child-friendly, educational"
        
        return final_prompt

    async def _submit_audio_generation(self, prompt: str, duration: int, video_clips: List[VideoClip]) -> Dict[str, Any]:
        """Soumet une requête de génération audio à FAL AI"""
        
        # Utiliser le premier clip vidéo valide comme référence (comme dans zseedance.json)
        reference_video_url = None
        for clip in video_clips:
            if clip.video_url and clip.status == "completed":
                reference_video_url = clip.video_url
                break
        
        # Paramètres basés sur le workflow zseedance.json
        audio_params = {
            "prompt": prompt,
            "duration": min(duration, 10),  # FAL AI limite souvent à 10 secondes
        }
        
        # Ajouter la vidéo de référence si disponible
        if reference_video_url:
            audio_params["video_url"] = reference_video_url
        
        url = f"{self.base_url}/{self.audio_model}"
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=audio_params, headers=headers) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Erreur API FAL AI {response.status}: {error_text}")
                
                return await response.json()

    async def _get_audio_result(self, request_id: str) -> Dict[str, Any]:
        """Récupère le résultat d'une génération audio"""
        
        url = f"{self.base_url}/{self.audio_model}/requests/{request_id}"
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}"
        }
        
        max_retries = 8
        retry_delay = 10  # secondes
        
        for attempt in range(max_retries):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Vérifier si la génération est terminée
                        if result.get("status") == "completed":
                            # Extraire l'URL audio du résultat
                            if "outputs" in result and len(result["outputs"]) > 0:
                                audio_url = result["outputs"][0]
                                return {"audio_url": audio_url}
                            else:
                                raise Exception("Aucun fichier audio généré")
                        
                        elif result.get("status") == "failed":
                            raise Exception(f"Génération audio échouée: {result.get('error', 'Erreur inconnue')}")
                        
                        # Si en cours, attendre et réessayer
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                    
                    else:
                        error_text = await response.text()
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            raise Exception(f"Erreur lors de la récupération audio {response.status}: {error_text}")
        
        raise Exception("Timeout: La génération audio n'a pas abouti dans les temps")

    async def validate_audio_url(self, url: str) -> bool:
        """Valide qu'une URL audio est accessible"""
        if not url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    return response.status == 200 and "audio" in response.headers.get("content-type", "")
        except:
            return False

    def estimate_audio_generation_time(self, duration: int) -> int:
        """Estime le temps de génération audio en secondes"""
        # Basé sur l'expérience avec FAL AI mmaudio-v2
        base_time = 60  # 1 minute de base
        duration_factor = duration * 2  # 2 secondes par seconde de vidéo
        
        return base_time + duration_factor 