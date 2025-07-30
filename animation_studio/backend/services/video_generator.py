import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from config import config
from models.schemas import Scene, VideoClip

class VideoGenerator:
    """Service de génération vidéo via Wavespeed AI SeedANce"""
    
    def __init__(self):
        self.base_url = config.WAVESPEED_BASE_URL
        self.api_key = config.WAVESPEED_API_KEY
        self.model = config.WAVESPEED_MODEL
    
    async def generate_video_clip(self, scene: Scene) -> VideoClip:
        """Génère un clip vidéo pour une scène donnée via Wavespeed AI"""
        
        # Préparer les paramètres selon l'API Wavespeed (inspiré de zseedance.json)
        video_params = {
            "aspect_ratio": config.VIDEO_ASPECT_RATIO,
            "duration": scene.duration,
            "prompt": scene.prompt
        }
        
        try:
            # 1. Soumettre la requête de génération
            video_data = await self._submit_video_generation(video_params)
            
            if not video_data or "data" not in video_data:
                raise Exception("Réponse invalide de l'API Wavespeed")
            
            prediction_id = video_data["data"]["id"]
            
            # 2. Attendre le traitement (équivalent du "Wait for clips" dans n8n)
            await asyncio.sleep(min(scene.duration * 10, 140))  # Attente adaptative basée sur la durée
            
            # 3. Récupérer le résultat
            result = await self._get_video_result(prediction_id)
            
            if not result or "video" not in result:
                raise Exception("Erreur lors de la récupération du résultat vidéo")
            
            return VideoClip(
                scene_number=scene.scene_number,
                video_url=result["video"]["url"],
                duration=scene.duration,
                status="completed"
            )
            
        except Exception as e:
            # Retourner un clip d'erreur plutôt que de faire échouer tout le pipeline
            return VideoClip(
                scene_number=scene.scene_number,
                video_url="",
                duration=scene.duration,
                status=f"failed: {str(e)}"
            )

    async def _submit_video_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Soumet une requête de génération vidéo à Wavespeed AI"""
        
        url = f"{self.base_url}/{self.model}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Erreur API Wavespeed {response.status}: {error_text}")
                
                return await response.json()

    async def _get_video_result(self, prediction_id: str) -> Dict[str, Any]:
        """Récupère le résultat d'une génération vidéo"""
        
        url = f"{self.base_url}/predictions/{prediction_id}/result"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        max_retries = 10
        retry_delay = 15  # secondes
        
        for attempt in range(max_retries):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Vérifier si la génération est terminée
                        if result.get("status") == "completed":
                            return result
                        elif result.get("status") == "failed":
                            raise Exception(f"Génération vidéo échouée: {result.get('error', 'Erreur inconnue')}")
                        
                        # Si en cours, attendre et réessayer
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                    
                    elif response.status == 404:
                        # Prédiction non trouvée, réessayer
                        if attempt < max_retries - 1:
                            await asyncio.sleep(retry_delay)
                            continue
                    
                    else:
                        error_text = await response.text()
                        raise Exception(f"Erreur lors de la récupération {response.status}: {error_text}")
        
        raise Exception("Timeout: La génération vidéo n'a pas abouti dans les temps")

    async def generate_all_clips(self, scenes: List[Scene]) -> List[VideoClip]:
        """Génère tous les clips vidéo pour une liste de scènes"""
        
        clips = []
        
        # Générer les clips en parallèle avec limitation pour éviter la surcharge
        semaphore = asyncio.Semaphore(3)  # Maximum 3 générations simultanées
        
        async def generate_with_semaphore(scene: Scene) -> VideoClip:
            async with semaphore:
                return await self.generate_video_clip(scene)
        
        # Créer les tâches
        tasks = [generate_with_semaphore(scene) for scene in scenes]
        
        # Exécuter toutes les tâches
        clips = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Traiter les résultats et les exceptions
        final_clips = []
        for i, result in enumerate(clips):
            if isinstance(result, Exception):
                # Créer un clip d'erreur
                final_clips.append(VideoClip(
                    scene_number=scenes[i].scene_number,
                    video_url="",
                    duration=scenes[i].duration,
                    status=f"failed: {str(result)}"
                ))
            else:
                final_clips.append(result)
        
        return final_clips

    async def validate_video_url(self, url: str) -> bool:
        """Valide qu'une URL vidéo est accessible"""
        if not url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(url) as response:
                    return response.status == 200
        except:
            return False

    def get_estimated_generation_time(self, scenes: List[Scene]) -> int:
        """Estime le temps de génération total en secondes"""
        
        # Temps de base par scène (basé sur l'expérience avec SeedANce)
        base_time_per_scene = 120  # 2 minutes par scène en moyenne
        
        # Temps supplémentaire selon la durée de la scène
        duration_factor = sum(scene.duration for scene in scenes) * 2
        
        # Temps de traitement parallèle (avec limitation à 3 simultanés)
        parallel_factor = max(1, len(scenes) / 3)
        
        total_time = (base_time_per_scene * parallel_factor) + duration_factor
        
        return int(total_time) 