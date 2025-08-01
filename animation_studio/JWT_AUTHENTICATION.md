# Authentification JWT avec Refresh Tokens

## Vue d'ensemble

L'application FRIDAY utilise maintenant un système d'authentification JWT (JSON Web Tokens) avec refresh tokens pour améliorer la sécurité. Ce système fonctionne en parallèle avec l'authentification Supabase existante pour assurer une transition en douceur.

## Architecture

### Backend (FastAPI)

#### Modules principaux :

1. **`utils/jwt_auth.py`** - Gestion des JWT tokens
   - Création et validation des access tokens (15 minutes)
   - Création et validation des refresh tokens (30 jours)
   - Middleware pour protéger les routes
   - Gestion automatique du refresh

2. **`services/auth_service.py`** - Service d'authentification
   - Intégration avec Supabase pour la gestion des utilisateurs
   - Création de profils utilisateur
   - Gestion des mots de passe

3. **`schemas/auth.py`** - Modèles Pydantic
   - Définition des structures de données pour l'API

#### Routes d'authentification :

- `POST /auth/login` - Connexion utilisateur
- `POST /auth/register` - Inscription utilisateur
- `POST /auth/refresh` - Rafraîchir un access token
- `POST /auth/logout` - Déconnexion (révocation des tokens)
- `GET /auth/profile` - Récupérer le profil utilisateur
- `PUT /auth/profile` - Mettre à jour le profil utilisateur
- `POST /auth/reset-password` - Réinitialisation de mot de passe
- `GET /auth/verify` - Vérifier la validité d'un token

### Frontend (React)

#### Service JWT :

**`services/jwtAuth.js`** - Service d'authentification frontend
- Gestion automatique des tokens
- Refresh automatique des tokens expirés
- File d'attente pour les requêtes échouées
- Intégration transparente avec l'API

#### Intégration :

Le composant `UserAccount.jsx` a été modifié pour :
- Essayer l'authentification JWT en premier
- Fallback vers Supabase si JWT échoue
- Gestion transparente des deux systèmes

## Configuration

### Variables d'environnement

Dans `backend/config.py` :

```python
# JWT Authentication
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
```

### Dépendances

Ajoutées dans `requirements.txt` :

```
PyJWT==2.8.0
email-validator==2.1.0
```

## Fonctionnalités de sécurité

### 1. Access Tokens courts (15 minutes)
- Limite l'exposition en cas de compromission
- Renouvellement automatique via refresh tokens

### 2. Refresh Tokens longs (30 jours)
- Permet une session prolongée sans compromettre la sécurité
- Stockage sécurisé côté serveur
- Révocation possible lors de la déconnexion

### 3. Gestion automatique du refresh
- Détection automatique des tokens expirés (401)
- Refresh transparent pour l'utilisateur
- File d'attente pour éviter les requêtes multiples

### 4. Révocation des tokens
- Suppression des refresh tokens lors de la déconnexion
- Invalidation immédiate des sessions

## Utilisation

### Connexion utilisateur

```javascript
// Frontend
import jwtAuthService from '../services/jwtAuth';

try {
  const result = await jwtAuthService.login(email, password);
  if (result.success) {
    // Connexion réussie
    console.log('Utilisateur connecté');
  }
} catch (error) {
  console.error('Erreur de connexion:', error);
}
```

### Requêtes authentifiées

```javascript
// Le service gère automatiquement l'authentification
const profile = await jwtAuthService.getProfile();
const updatedProfile = await jwtAuthService.updateProfile({
  first_name: "Nouveau",
  last_name: "Nom"
});
```

### Déconnexion

```javascript
await jwtAuthService.logout();
// Nettoie automatiquement les tokens et redirige
```

## Tests

### Script de test

Exécuter le script de test pour vérifier le fonctionnement :

```bash
cd backend
python test_jwt_auth.py
```

Le script teste :
1. Inscription d'un utilisateur
2. Connexion
3. Vérification du token
4. Récupération du profil
5. Mise à jour du profil
6. Refresh du token
7. Déconnexion
8. Tentative d'accès avec token révoqué

## Migration et compatibilité

### Stratégie de déploiement

1. **Phase 1** : Déploiement en parallèle
   - JWT et Supabase fonctionnent simultanément
   - Frontend essaie JWT en premier, puis Supabase

2. **Phase 2** : Migration complète
   - Suppression progressive de Supabase
   - Utilisation exclusive de JWT

3. **Phase 3** : Optimisation
   - Amélioration des performances
   - Ajout de fonctionnalités avancées

### Avantages de cette approche

- **Sécurité renforcée** : Tokens courts + refresh automatique
- **Expérience utilisateur préservée** : Pas de changement visible
- **Migration progressive** : Pas d'interruption de service
- **Flexibilité** : Possibilité de revenir à Supabase si nécessaire

## Sécurité

### Bonnes pratiques implémentées

1. **Tokens courts** : Access tokens de 15 minutes maximum
2. **Refresh sécurisé** : Tokens longs mais révocables
3. **Validation stricte** : Vérification des types de tokens
4. **Gestion d'erreurs** : Messages d'erreur sécurisés
5. **Nettoyage automatique** : Suppression des tokens expirés

### Recommandations de production

1. **Changer le JWT_SECRET** : Utiliser une clé forte et unique
2. **HTTPS obligatoire** : Toutes les communications en HTTPS
3. **Rate limiting** : Limiter les tentatives de connexion
4. **Monitoring** : Surveiller les tentatives d'accès
5. **Rotation des clés** : Changer périodiquement le JWT_SECRET

## Dépannage

### Problèmes courants

1. **Token expiré** : Le refresh automatique devrait résoudre le problème
2. **Erreur 401** : Vérifier la validité du token
3. **Erreur de connexion** : Vérifier les identifiants Supabase
4. **Refresh échoué** : L'utilisateur est déconnecté automatiquement

### Logs utiles

```bash
# Backend
tail -f backend/logs/app.log

# Frontend (Console navigateur)
# Vérifier les erreurs d'authentification
```

## Support

Pour toute question ou problème lié à l'authentification JWT, consulter :
- Les logs du backend
- La console du navigateur
- Le script de test `test_jwt_auth.py` 