import json
import asyncio
from typing import Dict, Any
from openai import AsyncOpenAI
from config import config
from models.schemas import StoryIdea, AnimationTheme

class IdeaGenerator:
    """Service de génération d'idées d'histoires pour enfants"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
    
    def get_theme_prompts(self) -> Dict[str, Dict[str, str]]:
        """Prompts spécialisés par thème inspirés de zseedance.json"""
        return {
            "space": {
                "base_concept": "a visually compelling space adventure for children",
                "elements": "spacecraft, planets, astronauts, friendly aliens, space stations",
                "setting": "cosmic environments, colorful nebulas, space stations, alien worlds",
                "mood": "adventurous, wonder-filled, educational, exciting"
            },
            "nature": {
                "base_concept": "a magical nature adventure for children", 
                "elements": "talking animals, magical trees, flowers, butterflies, forest creatures",
                "setting": "enchanted forests, flower meadows, crystal streams, fairy gardens",
                "mood": "peaceful, magical, educational, harmonious"
            },
            "adventure": {
                "base_concept": "a heroic adventure quest for children",
                "elements": "brave heroes, treasure maps, castles, dragons, magical artifacts",
                "setting": "fantasy kingdoms, mysterious caves, ancient castles, magical forests",
                "mood": "brave, exciting, inspiring, triumphant"
            },
            "animals": {
                "base_concept": "an animal friendship story for children",
                "elements": "cute animals, farms, jungles, oceans, animal families",
                "setting": "farms, jungles, savannas, oceans, cozy homes",
                "mood": "heartwarming, educational, funny, caring"
            },
            "magic": {
                "base_concept": "a magical fairy tale for children",
                "elements": "fairies, wizards, magic wands, potions, enchanted objects",
                "setting": "fairy kingdoms, magic schools, enchanted towers, mystical gardens",
                "mood": "whimsical, magical, wonder-filled, sparkling"
            },
            "friendship": {
                "base_concept": "a heartwarming friendship story for children",
                "elements": "diverse characters, cooperation, helping others, sharing, kindness",
                "setting": "schools, playgrounds, neighborhoods, community centers",
                "mood": "warm, caring, inspiring, joyful"
            }
        }
    
    def create_system_prompt(self, theme: AnimationTheme) -> str:
        """Crée le prompt système basé sur le style zseedance.json"""
        theme_data = self.get_theme_prompts()[theme.value]
        
        return f"""✅ Générateur d'Idées pour Dessins Animés Enfants (Inspiré de zseedance.json)

Rôle: Tu es un système créatif d'élite qui génère des concepts hyper-réalistes et engageants pour des dessins animés courts destinés aux enfants de 3-8 ans. Ton objectif est de livrer 1 idée unique, prête pour la production, qui soit éducative, amusante et visuellement magnifique.

ÉLÉMENTS OBLIGATOIRES:
- Une histoire claire avec début, milieu et fin adaptée aux enfants
- Des personnages attachants et mémorables 
- Des messages éducatifs subtils (amitié, partage, découverte, courage)
- Un univers visuel riche et coloré de style {config.CARTOON_STYLE}
- Du mouvement et de l'action adaptés à l'animation

THÈME SPÉCIFIQUE: {theme_data['base_concept']}
ÉLÉMENTS À INCLURE: {theme_data['elements']}
ENVIRONNEMENT: {theme_data['setting']}
AMBIANCE: {theme_data['mood']}

RÈGLES:
- Histoire complète en une phrase d'action claire
- Utiliser un langage visuel et cinématographique
- Éviter la violence ou les concepts effrayants
- Privilégier l'action, l'émerveillement et l'apprentissage
- Créer une caption accrocheuse avec 1 emoji et 3 hashtags enfants

EXIGENCES TECHNIQUES:
- L'audio doit décrire des sons doux et mélodieux adaptés aux enfants
- Le statut doit être "for production"
- Style visuel cohérent: {config.CARTOON_STYLE}

FORMAT DE SORTIE:
json
[
  {{
    "Caption": "🌟 Une aventure magique commence! Parfait pour l'imagination! #enfants #animation #magie",
    "Idea": "Idée complète de l'histoire en une phrase d'action claire et engageante",
    "Environment": "Description de l'environnement en moins de 20 mots",
    "Sound": "Description des effets sonores et ambiance musicale adaptés aux enfants",
    "Status": "for production"
  }}
]"""

    async def generate_story_idea(self, theme: AnimationTheme, duration: int) -> StoryIdea:
        """Génère une idée d'histoire basée sur le thème et la durée"""
        
        system_prompt = self.create_system_prompt(theme)
        
        user_prompt = f"""Génère une idée de dessin animé sur le thème "{theme.value}" d'une durée de {duration} secondes.

L'histoire doit être:
- Adaptée aux enfants de 3-8 ans
- Visuellement engageante pour l'animation
- Éducative et positive
- Complète avec début, milieu et fin
- Parfaite pour une durée de {duration} secondes

Respecte exactement le format JSON demandé."""

        try:
            response = await self.client.chat.completions.create(
                model=config.TEXT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # Créativité élevée
                max_tokens=1000
            )
            
            # Parser la réponse JSON
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON (enlever les balises markdown si présentes)
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            idea_data = json.loads(content)[0]
            
            return StoryIdea(**idea_data)
            
        except json.JSONDecodeError as e:
            # Fallback en cas d'erreur de parsing
            theme_data = self.get_theme_prompts()[theme.value]
            return StoryIdea(
                caption=f"🎬 Nouvelle aventure {theme.value}! #enfants #animation #{theme.value}",
                idea=f"Une histoire magique de {duration} secondes sur {theme_data['base_concept']}",
                environment=f"{theme_data['setting']}, style cartoon coloré",
                sound="Musique douce et effets sonores mélodieux pour enfants",
                status="for production"
            )
        
        except Exception as e:
            raise Exception(f"Erreur lors de la génération d'idée: {str(e)}")

    async def validate_idea(self, idea: StoryIdea) -> bool:
        """Valide qu'une idée est appropriée pour les enfants"""
        # Mots interdits pour les enfants
        forbidden_words = ["violent", "scary", "dark", "death", "fight", "war", "blood"]
        
        text_to_check = f"{idea.idea} {idea.caption} {idea.environment}".lower()
        
        for word in forbidden_words:
            if word in text_to_check:
                return False
        
        return True 