#!/usr/bin/env python3
"""
Script de test pour l'authentification JWT
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8007"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "Test123!"
TEST_FIRST_NAME = "Test"
TEST_LAST_NAME = "User"

async def test_jwt_auth():
    """Test complet de l'authentification JWT"""
    
    print("🧪 Test de l'authentification JWT")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Inscription
        print("\n1. Test d'inscription...")
        try:
            register_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "first_name": TEST_FIRST_NAME,
                "last_name": TEST_LAST_NAME
            }
            
            response = await client.post(
                f"{API_BASE_URL}/auth/register",
                json=register_data
            )
            
            if response.status_code == 200:
                register_result = response.json()
                print("✅ Inscription réussie")
                print(f"   Access Token: {register_result['access_token'][:50]}...")
                print(f"   Refresh Token: {register_result['refresh_token'][:50]}...")
                access_token = register_result['access_token']
                refresh_token = register_result['refresh_token']
            else:
                print(f"❌ Échec de l'inscription: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Erreur lors de l'inscription: {e}")
            return
        
        # Test 2: Connexion
        print("\n2. Test de connexion...")
        try:
            login_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
            
            response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                login_result = response.json()
                print("✅ Connexion réussie")
                print(f"   Access Token: {login_result['access_token'][:50]}...")
                print(f"   Refresh Token: {login_result['refresh_token'][:50]}...")
                access_token = login_result['access_token']
                refresh_token = login_result['refresh_token']
            else:
                print(f"❌ Échec de la connexion: {response.status_code}")
                print(f"   Réponse: {response.text}")
                return
                
        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {e}")
            return
        
        # Test 3: Vérification du token
        print("\n3. Test de vérification du token...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                f"{API_BASE_URL}/auth/verify",
                headers=headers
            )
            
            if response.status_code == 200:
                verify_result = response.json()
                print("✅ Vérification du token réussie")
                print(f"   User ID: {verify_result.get('user_id')}")
                print(f"   Email: {verify_result.get('email')}")
                print(f"   Valid: {verify_result.get('valid')}")
            else:
                print(f"❌ Échec de la vérification: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la vérification: {e}")
        
        # Test 4: Récupération du profil
        print("\n4. Test de récupération du profil...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                f"{API_BASE_URL}/auth/profile",
                headers=headers
            )
            
            if response.status_code == 200:
                profile_result = response.json()
                print("✅ Récupération du profil réussie")
                print(f"   ID: {profile_result.get('id')}")
                print(f"   Email: {profile_result.get('email')}")
                print(f"   Prénom: {profile_result.get('first_name')}")
                print(f"   Nom: {profile_result.get('last_name')}")
            else:
                print(f"❌ Échec de la récupération du profil: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du profil: {e}")
        
        # Test 5: Mise à jour du profil
        print("\n5. Test de mise à jour du profil...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            update_data = {
                "first_name": "Updated",
                "last_name": "User"
            }
            
            response = await client.put(
                f"{API_BASE_URL}/auth/profile",
                headers=headers,
                json=update_data
            )
            
            if response.status_code == 200:
                update_result = response.json()
                print("✅ Mise à jour du profil réussie")
                print(f"   Nouveau prénom: {update_result.get('first_name')}")
                print(f"   Nouveau nom: {update_result.get('last_name')}")
            else:
                print(f"❌ Échec de la mise à jour du profil: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour du profil: {e}")
        
        # Test 6: Refresh du token
        print("\n6. Test de refresh du token...")
        try:
            refresh_data = {"refresh_token": refresh_token}
            response = await client.post(
                f"{API_BASE_URL}/auth/refresh",
                json=refresh_data
            )
            
            if response.status_code == 200:
                refresh_result = response.json()
                print("✅ Refresh du token réussi")
                print(f"   Nouveau Access Token: {refresh_result['access_token'][:50]}...")
                print(f"   Refresh Token: {refresh_result['refresh_token'][:50]}...")
                access_token = refresh_result['access_token']
            else:
                print(f"❌ Échec du refresh: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur lors du refresh: {e}")
        
        # Test 7: Déconnexion
        print("\n7. Test de déconnexion...")
        try:
            logout_data = {"refresh_token": refresh_token}
            response = await client.post(
                f"{API_BASE_URL}/auth/logout",
                json=logout_data
            )
            
            if response.status_code == 200:
                logout_result = response.json()
                print("✅ Déconnexion réussie")
                print(f"   Message: {logout_result.get('message')}")
            else:
                print(f"❌ Échec de la déconnexion: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la déconnexion: {e}")
        
        # Test 8: Tentative d'accès avec un token révoqué
        print("\n8. Test d'accès avec token révoqué...")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(
                f"{API_BASE_URL}/auth/verify",
                headers=headers
            )
            
            if response.status_code == 401:
                print("✅ Accès correctement refusé avec token révoqué")
            else:
                print(f"⚠️ Accès inattendu: {response.status_code}")
                print(f"   Réponse: {response.text}")
                
        except Exception as e:
            print(f"❌ Erreur lors du test d'accès: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Tests terminés")

if __name__ == "__main__":
    print("🚀 Démarrage des tests JWT...")
    print(f"📡 API URL: {API_BASE_URL}")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(test_jwt_auth())
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrompus par l'utilisateur")
    except Exception as e:
        print(f"\n💥 Erreur générale: {e}") 