import asyncio
import aiohttp
from typing import List, Dict, Any
from config import config
from models.schemas import VideoClip, AudioTrack

class VideoAssembler:
    """Service d'assemblage vidéo final via FAL AI FFmpeg (basé sur le workflow zseedance.json)"""
    
    def __init__(self):
        self.fal_api_key = config.FAL_API_KEY
        self.ffmpeg_model = config.FAL_FFMPEG_MODEL
        self.base_url = "https://queue.fal.run"
    
    async def assemble_final_video(self, video_clips: List[VideoClip], audio_track: AudioTrack = None) -> str:
        """Assemble la vidéo finale à partir des clips et de l'audio"""
        
        # Filtrer les clips valides
        valid_clips = [clip for clip in video_clips if clip.video_url and clip.status == "completed"]
        
        if not valid_clips:
            raise Exception("Aucun clip vidéo valide pour l'assemblage")
        
        try:
            # 1. Créer la structure des pistes (inspirée de zseedance.json)
            tracks_config = self._create_tracks_configuration(valid_clips, audio_track)
            
            # 2. Soumettre la requête d'assemblage
            assembly_data = await self._submit_video_assembly(tracks_config)
            
            if not assembly_data or "request_id" not in assembly_data:
                raise Exception("Réponse invalide de l'API FAL AI FFmpeg")
            
            request_id = assembly_data["request_id"]
            
            # 3. Attendre le traitement (équivalent du "Wait for Final Video" dans n8n)
            total_duration = sum(clip.duration for clip in valid_clips)
            await asyncio.sleep(min(total_duration * 2, 120))  # Attente adaptative
            
            # 4. Récupérer le résultat
            result = await self._get_assembly_result(request_id)
            
            if not result or "video_url" not in result:
                raise Exception("Erreur lors de l'assemblage vidéo")
            
            return result["video_url"]
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'assemblage final: {str(e)}")

    def _create_tracks_configuration(self, video_clips: List[VideoClip], audio_track: AudioTrack = None) -> Dict[str, Any]:
        """Crée la configuration des pistes pour FFmpeg (basée sur zseedance.json)"""
        
        tracks = []
        
        # 1. Piste vidéo principale - assemblage séquentiel des clips
        video_keyframes = []
        current_timestamp = 0
        
        for clip in sorted(video_clips, key=lambda x: x.scene_number):
            keyframe = {
                "url": clip.video_url,
                "timestamp": current_timestamp,
                "duration": clip.duration
            }
            video_keyframes.append(keyframe)
            current_timestamp += clip.duration
        
        video_track = {
            "id": "1",
            "type": "video",
            "keyframes": video_keyframes
        }
        tracks.append(video_track)
        
        # 2. Piste audio si disponible
        if audio_track and audio_track.audio_url:
            audio_track_config = {
                "id": "2",
                "type": "audio",
                "keyframes": [
                    {
                        "url": audio_track.audio_url,
                        "timestamp": 0,
                        "duration": audio_track.duration
                    }
                ]
            }
            tracks.append(audio_track_config)
        
        return {"tracks": tracks}

    async def _submit_video_assembly(self, tracks_config: Dict[str, Any]) -> Dict[str, Any]:
        """Soumet une requête d'assemblage vidéo à FAL AI FFmpeg"""
        
        url = f"{self.base_url}/{self.ffmpeg_model}"
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}",
            "Content-Type": "application/json"
        }
        
        # Configuration additionnelle pour l'assemblage
        assembly_params = {
            **tracks_config,
            "output_format": "mp4",
            "resolution": config.VIDEO_RESOLUTION,
            "framerate": 24  # Standard pour les dessins animés
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=assembly_params, headers=headers) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    raise Exception(f"Erreur API FAL AI FFmpeg {response.status}: {error_text}")
                
                return await response.json()

    async def _get_assembly_result(self, request_id: str) -> Dict[str, Any]:
        """Récupère le résultat de l'assemblage vidéo"""
        
        url = f"{self.base_url}/{self.ffmpeg_model}/requests/{request_id}"
        
        headers = {
            "Authorization": f"Key {self.fal_api_key}"
        }
        
        max_retries = 12
        retry_delay = 15  # secondes
        
        for attempt in range(max_retries):
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Vérifier si l'assemblage est terminé
                        if result.get("status") == "completed":
                            # Extraire l'URL vidéo du résultat
                            if "video" in result:
                                return {"video_url": result["video"]["url"]}
                            elif "outputs" in result and len(result["outputs"]) > 0:
                                return {"video_url": result["outputs"][0]}
                            else:
                                raise Exception("Aucune vidéo assemblée générée")
                        
                        elif result.get("status") == "failed":
                            raise Exception(f"Assemblage vidéo échoué: {result.get('error', 'Erreur inconnue')}")
                        
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
                            raise Exception(f"Erreur lors de la récupération assemblage {response.status}: {error_text}")
        
        raise Exception("Timeout: L'assemblage vidéo n'a pas abouti dans les temps")

    async def create_simple_sequence(self, video_clips: List[VideoClip]) -> str:
        """Crée une séquence simple sans audio (méthode fallback)"""
        
        # Equivalent du node "List Elements" dans zseedance.json
        video_urls = [clip.video_url for clip in video_clips if clip.video_url and clip.status == "completed"]
        
        if len(video_urls) < 2:
            # Si moins de 2 clips, retourner le premier disponible
            return video_urls[0] if video_urls else ""
        
        # Configuration simplifiée pour séquence de base
        simple_config = {
            "tracks": [
                {
                    "id": "1",
                    "type": "video",
                    "keyframes": [
                        {"url": video_urls[i], "timestamp": i * 10, "duration": 10}
                        for i in range(min(len(video_urls), 3))  # Maximum 3 clips comme dans zseedance.json
                    ]
                }
            ]
        }
        
        try:
            assembly_data = await self._submit_video_assembly(simple_config)
            request_id = assembly_data["request_id"]
            
            await asyncio.sleep(60)  # Attente fixe pour séquence simple
            
            result = await self._get_assembly_result(request_id)
            return result["video_url"]
            
        except Exception as e:
            # Retourner le premier clip en cas d'échec
            return video_urls[0] if video_urls else ""

    async def validate_final_video(self, video_url: str) -> bool:
        """Valide que la vidéo finale est accessible et valide"""
        if not video_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.head(video_url) as response:
                    content_type = response.headers.get("content-type", "")
                    return response.status == 200 and "video" in content_type
        except:
            return False

    def estimate_assembly_time(self, video_clips: List[VideoClip]) -> int:
        """Estime le temps d'assemblage en secondes"""
        
        total_duration = sum(clip.duration for clip in video_clips)
        num_clips = len(video_clips)
        
        # Temps de base + facteur selon la complexité
        base_time = 60  # 1 minute de base
        duration_factor = total_duration  # 1 seconde par seconde de vidéo
        complexity_factor = num_clips * 10  # 10 secondes par clip supplémentaire
        
        return base_time + duration_factor + complexity_factor 