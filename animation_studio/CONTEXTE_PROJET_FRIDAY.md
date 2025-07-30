# 📋 CONTEXTE COMPLET DU PROJET FRIDAY

## 🎯 Vue d'ensemble du projet

**FRIDAY** est une application web complète de génération de contenu créatif pour enfants utilisant l'intelligence artificielle. Le projet combine un backend FastAPI avec un frontend React pour créer différents types de contenus : dessins animés, bandes dessinées, coloriages, histoires audio et comptines.

---

## 🏗️ Architecture Générale

### Structure du projet
```
backend/
├── 📁 saas/                     # Backend principal (FastAPI)
├── 📁 frontend/                 # Interface utilisateur (React + Vite)
├── 📁 cache/                    # Stockage des contenus générés
├── 📁 docs/                     # Documentation (legacy CrewAI - non utilisée)
├── 📁 static/                   # Fichiers statiques
├── 📁 __pycache__/             # Cache Python
└── 📄 Fichiers de configuration
```

### Technologies principales
- **Backend :** Python 3.11, FastAPI (pipeline custom sans CrewAI)
- **Frontend :** React 18, Vite, Framer Motion
- **IA :** OpenAI GPT-4o-mini, Stability AI, FAL AI, Udio, Wavespeed
- **Base de données :** Supabase (PostgreSQL)
- **Déploiement :** Local (dev), possibilité cloud

---

## 🔧 Configuration et Variables d'environnement

### Fichier `.env` principal (dans `saas/`)
```env
# APIs principales
OPENAI_API_KEY=sk-proj-[...] # Génération de texte et narration
STABILITY_API_KEY=sk-[...]   # Génération d'images (BD, coloriages)
FAL_API_KEY=[...]            # Génération vidéo et audio
GOAPI_API_KEY=[...]          # Génération musicale (Udio)
WAVESPEED_API_KEY=[...]      # Animation vidéo (SeedANce)

# Modèles configurés
TEXT_MODEL=gpt-4o-mini
IMAGE_MODEL=stability-ai
VIDEO_MODEL=sd3-large-turbo
TTS_MODEL=gpt-4o-mini-tts

# Fonctionnalités spécialisées
ENABLE_AI_BUBLES=false       # Bulles IA dans BD
ENABLE_SD3_BUBBLES=true      # Bulles SD3 intégrées
CARTOON_STYLE=2D cartoon animation, Disney style
CARTOON_DURATION=15
```

---

## 🖥️ Backend (saas/)

### Fichier principal : `main.py`
- **Port :** 8006 (configuré dans `frontend/src/config/api.js`)
- **Framework :** FastAPI avec CORS pour le frontend
- **Architecture :** Modulaire avec services séparés

### Endpoints principaux
```python
# Diagnostic
GET /diagnostic                    # Vérification des clés API

# Génération de contenu
POST /generate_rhyme/             # Comptines
POST /generate_audio_story/       # Histoires audio
POST /generate_coloring/          # Coloriages
POST /generate_comic/             # Bandes dessinées  
POST /generate_animation/         # Dessins animés

# TTS/STT
POST /tts                         # Text-to-Speech
POST /stt                         # Speech-to-Text

# Statiques
GET /cache/animations/{filename}  # Servir les vidéos générées
```

### Services (saas/services/)
```
├── complete_animation_pipeline.py    # Pipeline animation moderne (sans CrewAI)
├── comic_generator.py               # Génération de BD
├── coloring_generator.py            # Génération de coloriages
├── tts.py / stt.py                 # Audio
├── image_gen.py                     # Images via Stability AI
├── story_service.py                 # Gestion des histoires
├── musical_nursery_rhyme_service.py # Comptines musicales
└── video_assembler.py               # Assemblage vidéo

# Anciens services avec CrewAI (legacy, non utilisés)
├── animation_pipeline.py            # Ancien pipeline CrewAI
├── corrected_animation_service.py   # Service corrigé legacy
└── timeout_animation_service.py     # Service avec timeout legacy
```

### Pipeline d'animation (CompletAnimationPipeline)
**Architecture moderne remplaçant CrewAI :**
1. **Segmentation :** Découpe l'histoire en scènes (GPT-4o-mini)
2. **Style visuel :** Définition cohérente avec Stability AI
3. **Prompts optimisés :** Génération pour SD3-Turbo
4. **Clips vidéo :** Création via FAL/Wavespeed
5. **Assemblage final :** Montage et optimisation

**Avantages vs CrewAI :**
- Plus rapide et prévisible
- Moins de dépendances externes
- Contrôle total du workflow
- Debugging facilité

### Modèles de données (schemas/)
```python
# Animation
class AnimationRequest(BaseModel):
    style: AnimationStyle        # cartoon, anime, realistic...
    theme: AnimationTheme        # adventure, animals, magic...
    orientation: AnimationOrientation
    prompt: Optional[str]
    title: Optional[str]

class AnimationStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 🎨 Frontend (frontend/)

### Technologies
- **React 18** avec hooks modernes
- **Vite** pour le bundling rapide
- **Framer Motion** pour les animations
- **Axios** pour les requêtes API

### Architecture des composants
```
src/
├── App.jsx                      # Composant racine
├── components/                  # Composants réutilisables
│   ├── ContentTypeSelector.jsx  # Sélection du type de contenu
│   ├── AnimationSelector.jsx    # Paramètres d'animation
│   ├── ComicSelector.jsx        # Paramètres de BD
│   ├── ColoringSelector.jsx     # Paramètres de coloriage
│   ├── Header.jsx / Footer.jsx  # Layout
│   ├── History.jsx              # Historique utilisateur
│   └── LegalPages.jsx           # Pages légales
├── services/                    # Services API
│   ├── features.js              # Gestion des fonctionnalités
│   └── creations.js             # Sauvegarde créations
├── hooks/                       # Hooks personnalisés
│   └── useSupabaseUser.js       # Authentification
└── utils/                       # Utilitaires
    ├── pdfUtils.js              # Export PDF BD
    └── coloringPdfUtils.js      # Export PDF coloriage
```

### Gestion des fonctionnalités
```javascript
// Services dynamiques activables/désactivables
const DEFAULT_FEATURES = {
  animation: { enabled: true, name: 'Dessin animé', icon: '🎬' },
  comic: { enabled: true, name: 'Bande dessinée', icon: '📚' },
  coloring: { enabled: true, name: 'Coloriage', icon: '🎨' },
  audio: { enabled: true, name: 'Histoire', icon: '📖' },
  rhyme: { enabled: true, name: 'Comptine', icon: '🎵' }
};
```

### Configuration API
```javascript
// frontend/src/config/api.js
export const API_BASE_URL = 'http://localhost:8006';
export const API_ENDPOINTS = {
  generateAnimation: `${API_BASE_URL}/generate_animation/`,
  generateComic: `${API_BASE_URL}/generate_comic/`,
  // ...
};
```

---

## 🎯 Fonctionnalités Principales

### 1. 🎬 Dessins Animés
- **Pipeline :** CompletAnimationPipeline (architecture moderne sans CrewAI)
- **Durées :** 5-60 secondes configurables
- **Styles :** Cartoon, Anime, Réaliste, Aquarelle...
- **Thèmes :** Aventure, Animaux, Magie, Espace...
- **Technologie :** Stable Diffusion 3 + FAL AI + Wavespeed

### 2. 📚 Bandes Dessinées  
- **Format :** 4-6 cases par page
- **Styles artistiques :** Cartoon, Manga, Réaliste, Aquarelle
- **Personnages :** Prédéfinis ou personnalisés
- **Bulles :** Intégration automatique avec SD3
- **Export :** PDF haute qualité

### 3. 🎨 Coloriages
- **Thèmes :** Animaux, Licornes, Dinosaures, Nature...
- **Style :** Contours noirs, optimisé pour impression
- **Format :** PNG et PDF
- **Qualité :** Haute résolution

### 4. 📖 Histoires Audio
- **Génération :** GPT-4o-mini pour le texte
- **Narration :** TTS OpenAI avec voix configurables
- **Pagination :** Découpage automatique pour lecture
- **Longueur :** Adaptable selon l'âge

### 5. 🎵 Comptines
- **Contenu :** Rimes et mélodies pour enfants 3-8 ans
- **Musique :** Génération via Udio (optionnelle)
- **Format :** Texte + audio MP3
- **Thèmes :** Animaux, Nature, Transport, Couleurs...

---

## 🗄️ Base de Données (Supabase)

### Configuration
```javascript
// frontend/src/supabaseClient.js
const supabaseUrl = 'https://xfbmdeuzuyixpmouhqcv.supabase.co'
const supabaseKey = '[clé publique]'
```

### Tables principales
```sql
-- Profils utilisateurs
CREATE TABLE profiles (
  id uuid REFERENCES auth.users ON DELETE CASCADE,
  prenom text,
  nom text,
  date_naissance date,
  preferences jsonb,
  created_at timestamp DEFAULT now()
);

-- Créations sauvegardées
CREATE TABLE creations (
  id uuid DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES profiles(id),
  type text, -- 'animation', 'comic', 'coloring'...
  title text,
  content jsonb,
  file_urls text[],
  created_at timestamp DEFAULT now()
);
```

### Sécurité RLS (Row Level Security)
- Politiques configurées pour l'isolation par utilisateur
- Authentification via Auth.js

---

## 📁 Système de Cache

### Structure des caches
```
cache/
├── animations/          # Vidéos MP4 générées (pipeline moderne)
├── audio/              # Fichiers audio TTS
├── comics/             # BD finales avec bulles
├── comics_raw/         # BD sans bulles
├── coloring/           # Images de coloriage
├── bubble_integrations/ # Bulles SD3
└── crewai_animations/  # Legacy (compatibilité, non utilisé)
```

### Gestion des fichiers
- **Nommage :** UUID + timestamp pour unicité
- **Formats :** MP4 (vidéo), PNG (images), MP3 (audio)
- **Accès :** Endpoints dédiés avec support Range (streaming)

---

## 🔄 Processus de Génération

### Animation complète (exemple)
```python
# 1. Réception de la demande
{
  "story": "Une aventure dans la forêt magique",
  "duration": 15,
  "style": "cartoon",
  "theme": "adventure"
}

# 2. Segmentation intelligente
scenes = [
  {"text": "Un enfant entre dans la forêt", "duration": 3},
  {"text": "Il découvre une créature magique", "duration": 4},
  {"text": "Ils deviennent amis", "duration": 3},
  {"text": "Ensemble ils trouvent un trésor", "duration": 5}
]

# 3. Génération des prompts visuels
prompts = [
  "cartoon child walking into magical forest, Disney style, bright colors",
  "cartoon magical creature, friendly, glowing, forest background",
  # ...
]

# 4. Création des clips via SD3-Turbo
# 5. Assemblage et optimisation finale
```

### Bande Dessinée (workflow)
```python
# 1. Génération du scénario (GPT-4o-mini)
# 2. Création des images case par case (Stability AI)
# 3. Génération des dialogues appropriés
# 4. Intégration des bulles (SD3 ou overlay)
# 5. Assemblage et export PDF
```

---

## ⚙️ Configuration du Développement

### Démarrage local
```bash
# Backend (port 8006)
cd saas/
python -m uvicorn main:app --reload --port 8006

# Frontend (port 5175)
cd frontend/
npm run dev
```

### Variables d'environnement requises
```env
# Minimum pour fonctionner
OPENAI_API_KEY=sk-proj-[...] # ✅ Obligatoire
STABILITY_API_KEY=sk-[...]   # ✅ Pour BD/coloriages

# Optionnel selon fonctionnalités
FAL_API_KEY=[...]           # Pour animations avancées
GOAPI_API_KEY=[...]         # Pour comptines musicales
WAVESPEED_API_KEY=[...]     # Pour SeedANce
```

### Dépendances principales
```python
# Backend (requirements.txt) - Note: CrewAI présent mais non utilisé
fastapi==0.115.12
openai==1.77.0
stability-sdk==0.8.6
crewai==0.130.0        # Legacy - non utilisé dans le pipeline actuel
pillow==11.2.1
aiohttp==3.9.1
opencv-python==4.10.0.84
uvicorn==0.23.2
```

```json
// Frontend (package.json)
{
  "react": "^18.2.0",
  "framer-motion": "^10.18.0",
  "@supabase/supabase-js": "^2.50.0",
  "axios": "^1.10.0",
  "jspdf": "^3.0.1"
}
```

---

## 🧪 Tests et Validation

### Scripts de validation
- `validation_finale.py` : Tests complets du pipeline
- `validate_stability_ai.py` : Vérification Stability AI
- `validate_pipeline.py` : Tests des services individuels

### Diagnostic en temps réel
```javascript
// Frontend: vérification des APIs
GET /diagnostic
{
  "openai_configured": true,
  "stability_configured": true,
  "fal_configured": true,
  "text_model": "gpt-4o-mini"
}
```

---

## 📊 Styles et Thèmes Supportés

### Styles d'animation (animation_config/animation_styles.py)
```python
FRIDAY_ANIMATION_STYLES = {
    'cartoon': {
        'name': '2D Cartoon',
        'sd_prompt': 'cartoon style, 2D animation, colorful, Disney-style',
        'recommended_model': 'dreamshaper_8.safetensors'
    },
    'anime': {
        'name': 'Anime',
        'sd_prompt': 'anime style, manga style, Japanese animation',
        'recommended_model': 'animePastelDream_softBakedVae.safetensors'
    }
    # ... 6 styles total
}
```

### Thèmes disponibles
- **Aventure :** Exploration, quêtes, découvertes
- **Animaux :** Ferme, jungle, océan, domestiques  
- **Magie :** Fées, sorciers, potions, créatures
- **Espace :** Planètes, astronautes, aliens
- **Amitié :** Relations, entraide, coopération
- **Nature :** Forêts, jardins, saisons

---

## 🔐 Sécurité et Confidentialité

### Authentification
- **Supabase Auth** avec gestion des sessions
- **RLS (Row Level Security)** pour l'isolation des données
- **Policies** automatiques sur toutes les tables

### Confidentialité
- Pas de stockage permanent des prompts utilisateur
- Cache local temporaire avec nettoyage automatique
- Conformité RGPD (pages légales incluses)

### APIs externes
- Clés API stockées uniquement côté serveur
- Rotation des clés recommandée
- Monitoring des quotas d'utilisation

---

## 🚀 Déploiement et Production

### Architecture recommandée
```
Load Balancer
├── Frontend (Vercel/Netlify)
├── Backend (Railway/Render)
├── Database (Supabase managed)
└── Storage (Supabase/AWS S3)
```

### Variables de production
```env
# Sécurité
CORS_ORIGINS=https://votre-domaine.com
DATABASE_URL=postgresql://...
JWT_SECRET=...

# Performance  
REDIS_URL=redis://...          # Cache distribué
CDN_URL=https://cdn...         # Assets statiques
```

### Monitoring recommandé
- Logs applicatifs (FastAPI)
- Métriques de performance (temps génération)
- Monitoring des quotas API
- Alertes sur erreurs critiques

---

## 📈 Évolutions et Roadmap

### Migration technique effectuée
- **✅ Abandon de CrewAI :** Migration vers pipeline custom plus performant
- **✅ Pipeline unifié :** CompletAnimationPipeline remplace l'ancien système
- **✅ Optimisation :** Réduction des temps de génération
- **✅ Stabilité :** Moins de points de défaillance

### Fonctionnalités en développement
- **Multi-langues :** Support anglais/espagnol
- **Personnalisation avancée :** Avatar persistants
- **Collaboration :** Projets partagés entre utilisateurs
- **Mobile :** Application React Native

### Améliorations techniques
- **Pipeline GPU :** Migration vers des modèles locaux
- **Cache intelligent :** Système de recommandations
- **API GraphQL :** Pour requêtes complexes
- **Microservices :** Séparation par fonctionnalité

---

## 🛠️ Maintenance et Troubleshooting

### Problèmes courants

1. **Clés API expirées**
   ```bash
   # Vérification
   curl http://localhost:8006/diagnostic
   ```

2. **Erreurs de génération**
   ```python
   # Logs détaillés dans
   saas/logs/generation_errors.log
   ```

3. **Problèmes de cache**
   ```bash
   # Nettoyage manuel
   rm -rf cache/animations/*
   ```

### Logs principaux
- Backend FastAPI : Console et fichiers
- Frontend React : Console navigateur + Network
- Supabase : Dashboard intégré

### Support et documentation
- **Email :** contact@friday.com
- **Documentation :** /docs (auto-générée FastAPI)
- **Issues :** GitHub repository

---

## 📝 Notes de Développement

### Conventions de code
- **Python :** PEP 8, type hints obligatoires
- **JavaScript :** ESLint, Prettier, hooks modernes
- **CSS :** BEM methodology, variables CSS

### Git workflow
- **Branches :** main, develop, feature/*
- **Commits :** Conventional commits
- **CI/CD :** GitHub Actions (à configurer)

### Base de code
- **Langues :** Français (UI), Anglais (code/comments)
- **Documentation :** Markdown avec exemples
- **Tests :** Pytest (backend), Jest (frontend)
- **Architecture :** Pipeline custom remplaçant CrewAI pour plus de contrôle

---

*Document généré automatiquement le 20 juillet 2025*  
*Version du projet : 2.0 (Pipeline moderne sans CrewAI)*  
*Dernière mise à jour : Analyse complète du codebase avec corrections*
