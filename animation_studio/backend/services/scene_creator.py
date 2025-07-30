import json
import math
from typing import List
from openai import AsyncOpenAI
from config import config
from models.schemas import StoryIdea, Scene

class SceneCreator:
    """Service de création de scènes détaillées pour l'animation"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    
    def calculate_scene_distribution(self, total_duration: int) -> List[int]:
        """Calcule la distribution optimale des scènes selon la durée totale"""
        if total_duration <= 30:
            # 3 scènes pour les courtes durées
            return [total_duration // 3] * 3
        elif total_duration <= 60:
            # 4 scènes pour 1 minute
            base_duration = total_duration // 4
            return [base_duration] * 4
        elif total_duration <= 120:
            # 5 scènes pour 2 minutes
            base_duration = total_duration // 5
            return [base_duration] * 5
        else:
            # 6-8 scènes pour les plus longues durées
            num_scenes = min(8, max(6, total_duration // 30))
            base_duration = total_duration // num_scenes
            return [base_duration] * num_scenes

    def create_scene_system_prompt(self) -> str:
        """Prompt système pour la génération de scènes inspiré de zseedance.json"""
        return f"""✅ Générateur de Scènes Cinématographiques pour Dessins Animés Enfants

Rôle: Tu es un générateur de prompts cinématographiques qui produit des scènes ultra-réalistes pour dessins animés, conçues pour la génération vidéo haute définition.

ÉLÉMENTS OBLIGATOIRES (pour chaque scène):
- Décrire l'action/mouvement principal en cours
- Inclure des détails visuels spécifiques et colorés
- Utiliser des termes cinématographiques techniques (plan rapproché, travelling, zoom)
- Optimisé pour le style: {config.CARTOON_STYLE}
- Personnages en mouvement constant, jamais statiques
- Environnement interactif avec effets visuels

STYLE VISUEL:
- Toujours décrire comme une vraie prise, capturée par un équipement cinématographique professionnel
- Utiliser des termes visuels cinématographiques (panoramique lent, plan moyen, dolly aérien, zoom arrière)
- Éviter le langage poétique ou métaphorique. Utiliser uniquement le réalisme visuel et scientifique
- Explorer différentes phases: approche, arrivée, interaction, réaction de l'environnement, révélation

EXIGENCES TECHNIQUES:
- Chaque scène doit avoir une action claire et spécifique
- Décrire les mouvements de caméra et les angles
- Inclure les interactions avec l'environnement
- Style cohérent: animation 2D colorée, style Disney/cartoon
- Éviter les répétitions entre les scènes

PROBLÈMES À ÉVITER:
- Pas de descriptions statiques ou d'images fixes
- Ne pas réutiliser les mêmes mouvements à travers les scènes
- Les personnages ne doivent jamais être inactifs - toujours faire quelque chose de cinématographique
- Ne pas se contenter de décrire des jeux de lumière. Inclure des phénomènes tactiles et interactifs

FORMAT DE SORTIE:
json
{{
  "Idea": "L'idée principale de l'histoire",
  "Environment": "L'environnement général",
  "Sound": "Description audio globale",
  "Scene 1": "Description technique de la première scène avec mouvements et actions spécifiques",
  "Scene 2": "Description technique de la deuxième scène...",
  "Scene N": "Description de la dernière scène..."
}}"""

    async def create_scenes_from_idea(self, story_idea: StoryIdea, duration: int) -> List[Scene]:
        """Crée des scènes détaillées à partir d'une idée d'histoire"""
        
        scene_durations = self.calculate_scene_distribution(duration)
        num_scenes = len(scene_durations)
        
        system_prompt = self.create_scene_system_prompt()
        
        user_prompt = f"""Crée {num_scenes} scènes cinématographiques détaillées basées sur cette idée d'histoire:

IDÉE: {story_idea.idea}
ENVIRONNEMENT: {story_idea.environment}
SON: {story_idea.sound}
DURÉE TOTALE: {duration} secondes
DURÉES DES SCÈNES: {scene_durations} secondes chacune

L'histoire doit être divisée en {num_scenes} scènes cohérentes qui racontent l'histoire complète:
- Début engageant (scènes 1-2)
- Développement/action (scènes milieu) 
- Conclusion satisfaisante (dernières scènes)

Chaque scène doit:
- Être optimisée pour la génération vidéo SeedANce/Wavespeed
- Inclure des mouvements et actions spécifiques
- Utiliser des termes cinématographiques précis
- Être adaptée aux enfants de 3-8 ans
- Avoir une progression narrative claire

Respecte exactement le format JSON demandé avec Scene 1, Scene 2, etc."""

        try:
            response = await self.client.chat.completions.create(
                model=config.TEXT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,  # Créativité contrôlée
                max_tokens=2000
            )
            
            # Parser la réponse JSON
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            scenes_data = json.loads(content)
            
            # Extraire les scènes
            scenes = []
            for i in range(num_scenes):
                scene_key = f"Scene {i + 1}"
                if scene_key in scenes_data:
                    # Créer le prompt optimisé pour SeedANce
                    optimized_prompt = self.optimize_prompt_for_seedance(
                        scenes_data[scene_key],
                        story_idea.environment,
                        i + 1
                    )
                    
                    scene = Scene(
                        scene_number=i + 1,
                        description=scenes_data[scene_key],
                        duration=scene_durations[i],
                        prompt=optimized_prompt
                    )
                    scenes.append(scene)
            
            return scenes
            
        except json.JSONDecodeError as e:
            # Fallback avec scènes génériques
            return self.create_fallback_scenes(story_idea, scene_durations)
        
        except Exception as e:
            raise Exception(f"Erreur lors de la création des scènes: {str(e)}")

    def optimize_prompt_for_seedance(self, scene_description: str, environment: str, scene_number: int) -> str:
        """Optimise le prompt pour la génération vidéo SeedANce/Wavespeed"""
        
        # Préfixe spécifique au style cartoon pour enfants
        style_prefix = f"VIDEO THEME: {config.CARTOON_STYLE}, bright colors, child-friendly"
        
        # Description de la scène optimisée
        scene_optimized = f"WHAT HAPPENS IN THE VIDEO: {scene_description}"
        
        # Environnement contextualisé
        environment_optimized = f"WHERE THE VIDEO IS SHOT: {environment}, animated cartoon style"
        
        # Assemblage final selon le format du workflow zseedance.json
        final_prompt = f"{style_prefix} | {scene_optimized} | {environment_optimized}"
        
        return final_prompt

    def create_fallback_scenes(self, story_idea: StoryIdea, scene_durations: List[int]) -> List[Scene]:
        """Crée des scènes de fallback en cas d'erreur"""
        scenes = []
        
        # Scènes génériques basées sur l'idée
        scene_templates = [
            "Introduction du personnage principal dans l'environnement coloré",
            "Le personnage découvre quelque chose d'intéressant et s'approche",
            "Action principale de l'histoire avec mouvements dynamiques",
            "Résolution positive avec apprentissage ou découverte",
            "Conclusion joyeuse avec personnage satisfait"
        ]
        
        for i, duration in enumerate(scene_durations):
            template = scene_templates[min(i, len(scene_templates) - 1)]
            
            scene = Scene(
                scene_number=i + 1,
                description=f"{template} - {story_idea.idea}",
                duration=duration,
                prompt=self.optimize_prompt_for_seedance(
                    template,
                    story_idea.environment,
                    i + 1
                )
            )
            scenes.append(scene)
        
        return scenes

    def extract_scenes_from_text(self, text: str) -> List[str]:
        """Extrait les descriptions de scènes d'un texte (méthode utilitaire du workflow n8n)"""
        scenes = []
        
        # Recherche de patterns "Scene X:" ou "Scène X:"
        import re
        scene_pattern = r'(?:Scene|Scène)\s*(\d+):\s*(.+?)(?=(?:Scene|Scène)\s*\d+:|$)'
        matches = re.findall(scene_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            scene_text = match[1].strip()
            if scene_text:
                scenes.append(scene_text)
        
        return scenes 